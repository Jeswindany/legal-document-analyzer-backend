interface ParamTableProps {
  params: {
    name: string;
    type: string;
    required: boolean;
    description: string;
    default?: string;
  }[];
}

export function ParamTable({ params }: ParamTableProps) {
  return (
    <div className="border border-border rounded-md divide-y divide-border">
      {params.map((p) => (
        <div key={p.name} className="param-row px-4">
          <div className="min-w-[140px]">
            <span className="param-name">{p.name}</span>
            {p.required && <span className="param-required ml-2">required</span>}
          </div>
          <div className="flex-1">
            <span className="param-type">{p.type}</span>
            {p.default && (
              <span className="param-type ml-2">default: {p.default}</span>
            )}
            <p className="text-sm text-muted-foreground mt-0.5">{p.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
